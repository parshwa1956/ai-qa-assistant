import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserAttribute,
  CognitoUserPool,
} from 'amazon-cognito-identity-js'

const poolId = import.meta.env.VITE_COGNITO_USER_POOL_ID
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID

const pool = new CognitoUserPool({
  UserPoolId: poolId,
  ClientId: clientId,
})

export function getCurrentUser(): CognitoUser | null {
  return pool.getCurrentUser()
}

export function signUp(email: string, password: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const attrs = [new CognitoUserAttribute({ Name: 'email', Value: email })]
    pool.signUp(email, password, attrs, [], (err) => {
      if (err) reject(err)
      else resolve()
    })
  })
}

export function signIn(email: string, password: string): Promise<string> {
  const user = new CognitoUser({ Username: email, Pool: pool })
  const auth = new AuthenticationDetails({ Username: email, Password: password })
  return new Promise((resolve, reject) => {
    user.authenticateUser(auth, {
      onSuccess: (session) => resolve(session.getIdToken().getJwtToken()),
      onFailure: (err) => reject(err),
    })
  })
}

export function signOut(): void {
  const user = pool.getCurrentUser()
  if (user) user.signOut()
}

export function forgotPassword(email: string): Promise<void> {
  const user = new CognitoUser({ Username: email, Pool: pool })
  return new Promise((resolve, reject) => {
    user.forgotPassword({
      onSuccess: () => resolve(),
      onFailure: (err) => reject(err),
    })
  })
}

export function confirmPassword(email: string, code: string, newPassword: string): Promise<void> {
  const user = new CognitoUser({ Username: email, Pool: pool })
  return new Promise((resolve, reject) => {
    user.confirmPassword(code, newPassword, {
      onSuccess: () => resolve(),
      onFailure: (err) => reject(err),
    })
  })
}

export function getIdToken(): Promise<string | null> {
  const user = pool.getCurrentUser()
  if (!user) return Promise.resolve(null)
  return new Promise((resolve) => {
    user.getSession((err: Error | null, session: { isValid: () => boolean; getIdToken: () => { getJwtToken: () => string } } | null) => {
      if (err || !session?.isValid()) {
        resolve(null)
        return
      }
      resolve(session.getIdToken().getJwtToken())
    })
  })
}
